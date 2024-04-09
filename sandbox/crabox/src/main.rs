use std::process::Command;

fn main(){
println!("hello");

let output=Command::new("ls").output().expect("22333");
let ls_list=String::from_utf8(output.stdout).unwrap();

println!("{}",ls_list);

__EOF__
}

// __EOF__