let greet = (name : string) => {
      console.log("Hello", name)
}

let get = (arr: [string], idx: int) => {
      return arr[idx]
}

let arr = ["World"]

greet(get(arr, 1));
