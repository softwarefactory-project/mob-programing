use std::io::Read;
use std::io::Result;
use std::io::{BufRead, BufReader};

pub struct BufLines<R: Read> {
    reader: BufReader<R>,
    buffer: String,
    pos: usize,
}

impl<R: Read> Iterator for BufLines<R> {
    type Item = Result<(usize, String)>;

    fn next(&mut self) -> Option<Self::Item> {
        if !self.buffer.is_empty() {
            let pos = self.pos;
            let result = if let Some((sub_line, rest)) = self.buffer.split_once("\\n") {
                let result = sub_line.to_string();
                self.buffer = rest.to_string();
                result
            } else {
                self.pos += 1;
                let result = self.buffer.clone();
                self.buffer.clear();
                result
            };
            Some(Ok((pos, result)))
        } else {
            match self.reader.read_line(&mut self.buffer) {
                Ok(n) if n > 0 => {
                    self.buffer = self
                        .buffer
                        .trim_end_matches(|c| matches!(c, '\n' | '\r'))
                        .to_string();
                    self.next()
                }
                Ok(_) => None,
                Err(e) => Some(Err(e)),
            }
        }
    }
}

impl<R: Read> BufLines<R> {
    pub fn new(read: R) -> BufLines<R> {
        BufLines {
            reader: BufReader::new(read),
            buffer: String::new(),
            pos: 0,
        }
    }
}

/*
fn main() -> Result<()> {
    for line_result in BufLines::new(std::io::stdin()) {
        let (pos, line) = line_result?;
        println!("{} | {}", pos, line)
    }
    Ok(())
}
*/

fn is_anomaly(s: &str) -> bool {
    s.contains("anomaly")
}

struct LogLine {
    pos: usize,
    line: String,
    before: Vec<String>,
    after: Vec<String>,
}

struct LogLines<R: Read> {
    inner: BufLines<R>,
    before: Vec<String>,
    current: Option<LogLine>,
}

impl<R: Read> Iterator for LogLines<R> {
    type Item = Result<LogLine>;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(next) = self.inner.next() {
            match next {
                Err(e) => Some(Err(e)),
                Ok((pos, line)) => {
                    if is_anomaly(&line) {
                        if let Some(current) = self.current {
                            // We are processing an anomaly
                            let result = current;
                            self.current = Some(LogLine {
                                pos,
                                line,
                                before: self.before.clone(),
                                after: Vec::new(),
                            });
                            self.before = Vec::new();
                            Some(Ok(current))
                        } else {
                            // This is a new anomaly
                            self.current = Some(LogLine {
                                pos,
                                line,
                                before: self.before.clone(),
                                after: Vec::new(),
                            });
                            None
                        }
                    } else {
                        if let Some(current) = self.current {
                            current.after.push(line);
                            if current.after.len() > 2 {
                                self.current = None
                                Some(Ok(current))
                            }
                        } else {
                            self.before.push(line);
                            if self.before.len() > 2 {
                                self.before.rotate_left(1);
                            }
                            self.next()
                        }
                    }
                }
            }
        } else {
            if let Some(current) = self.current {
                Some(Ok(current))
            } else {
                None
            }
        }
    }
}
