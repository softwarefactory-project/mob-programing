let greet = (name: string) => {
  Js.log2("Hello", name)
}

let arr = ["World"]

switch (arr->Belt.List.get(1)) {
  | Some(x) => greet(x)
  | None => Js.log("Oops, no value was found")
};
