use clap::{App, Arg};
use elasticsearch::{
    http::transport::{SingleNodeConnectionPool, TransportBuilder},
    BulkOperation, BulkParts, Elasticsearch, Error, DEFAULT_ADDRESS,
};
use jwalk::Parallelism::RayonNewPool;
use jwalk::WalkDir;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::hash_map::DefaultHasher;
use std::fs::File;
use std::hash::Hash;
use std::hash::Hasher;
use std::io::{self, BufRead};
use std::path::Path;
use std::path::PathBuf;
use std::thread;
use url::Url;

#[derive(Debug, Hash, Serialize, Deserialize, PartialEq)]
pub struct LogLine {
    pub file_name: String,
    pub line_nr: usize,
    pub line: String,
    pub build_uuid: String,
}

impl LogLine {
    pub fn id(&self) -> String {
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish().to_string()
    }
}

async fn index_loglines(client: &Elasticsearch, loglines: &[LogLine]) -> Result<(), Error> {
    let body: Vec<BulkOperation<_>> = loglines
        .iter()
        .map(|p| {
            let id = p.id();
            BulkOperation::index(p).id(&id).routing(&id).into()
        })
        .collect();

    let response = client
        .bulk(BulkParts::Index("scrapydoo"))
        .body(body)
        .send()
        .await?;

    let json: Value = response.json().await?;

    if json["errors"].as_bool().unwrap() {
        let failed: Vec<&Value> = json["items"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|v| !v["error"].is_null())
            .collect();
        println!("Errors whilst indexing. Failures: {}", failed.len());
    }

    Ok(())
}

async fn process_logfile(client: &Elasticsearch, logfile: PathBuf) -> Result<(), Error> {
    println!("{:?} Processing: {:?}", thread::current().id(), logfile);
    let file_name = logfile.to_str().unwrap_or("N/A").to_string();
    match read_lines(logfile) {
        Ok(lines) => {
            let vec_log_lines: Result<Vec<_>, _> = lines
                .enumerate()
                .map(|(i, line_e)| match line_e {
                    Ok(line) => Ok(LogLine {
                        line: line,
                        line_nr: i,
                        build_uuid: From::from("tata"),
                        file_name: file_name.clone(),
                    }),
                    Err(e) => Err(e),
                })
                .collect();
            match vec_log_lines {
                Ok(log_lines) if !log_lines.is_empty() => {
                    println!("Indexing {:?} line(s)...", log_lines.len());
                    index_loglines(client, &log_lines).await?
                }
                Ok(_) => println!("Empty file."),
                Err(e) => println!("Can't read line: {}", e),
            }
        }
        Err(e) => println!("Can't read {}", e),
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let client = create_client().unwrap();
    let matches = App::new("Scrapydoo")
        .arg(
            Arg::with_name("dir")
                .long("dir")
                .takes_value(true)
                .required(true)
                .help("The directory to index"),
        )
        .get_matches();

    let dir = matches.value_of("dir").unwrap();
    println!("Indexing {} root directory", dir);
    for entry in WalkDir::new(dir).parallelism(RayonNewPool(5)) {
        match entry {
            Err(e) => println!("Can't read dir: {}", e),
            Ok(x) => {
                if !x.file_type.is_dir() {
                    process_logfile(&client, x.parent_path.join(x.file_name)).await?;
                }
            }
        }
    }
    Ok(())
}

// The output is wrapped in a Result to allow matching on errors
// Returns an Iterator to the Reader of the lines of the file.
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

// copy pasta from github.com/elastic/elasticsearch-rs/elasticsearch/examples/index_questions_answers/main.rs
fn create_client() -> Result<Elasticsearch, Error> {
    fn cluster_addr() -> String {
        match std::env::var("ELASTICSEARCH_URL") {
            Ok(server) => server,
            Err(_) => DEFAULT_ADDRESS.into(),
        }
    }
    let url = Url::parse(cluster_addr().as_ref()).unwrap();
    let conn_pool = SingleNodeConnectionPool::new(url);
    let builder = TransportBuilder::new(conn_pool);
    let transport = builder.build()?;
    Ok(Elasticsearch::new(transport))
}
