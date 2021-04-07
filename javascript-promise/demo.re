let delay = (resolve, value) => {
  Js.Global.setTimeout(() => resolve(. value), 1000)->ignore;
};

let react_component = () => {
  let promise = Js.Promise.make((~resolve, ~reject) => delay(resolve, 42));

  let setState = (x: int) => {
    Js.log2("State is changed to", x);
  };

  // How to get the 42?
  promise
  |> Js.Promise.then_(value => {
       setState(value);
       Js.Promise.resolve(41);
     })
  |> Js.Promise.then_(value => setState(value)->Js.Promise.resolve);
};

Js.log("begin");
react_component();
Js.log("over");
