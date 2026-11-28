use std::io::{self, BufRead};

fn main() -> io::Result<()> {
    println!("{}", std::env::consts::ARCH);
    for line in io::stdin().lock().lines() {
        let line = line?;
        let fields: Vec<_> = line.split('\t').collect();
        println!("{}", classify::classify(fields[0], &fields[1..])?.unwrap_or_default());
    }
    Ok(())
}
