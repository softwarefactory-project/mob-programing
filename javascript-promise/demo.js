let delay = (resolve, value) => {
  setTimeout(() => resolve(value), 1000);
};

let react_component = () => {
  let promise = new Promise((resolve, reject, x) => {
    delay(resolve, 42);
  });

  let setState = (x) => {
    console.log("State is changed to ", x);
  };

  // How to get the 42?
  promise
    .then((value) => {
      setState(value);
      return Promise.resolve(41);
    })
    .then(setState);
};

console.log("begin");
react_component();
console.log("over");
