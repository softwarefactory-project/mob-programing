struct Resource(usize);

fn create_resource(count: usize) -> Result<Resource, String> {
    println!("Creating resource: {}", count);
    if count < 10 {
        Ok(Resource(count))
    } else {
        Err("Too many resources".to_string())
    }
}

fn deploy_sf() -> Result<(), String> {
    let _db = create_resource(9000)?;
    let _zuul = create_resource(1)?;
    Ok(())
}

fn main() {
    match deploy_sf() {
        Ok(_) => println!("Deployed!"),
        Err(e) => println!("Ooops: {}", e),
    }
}
