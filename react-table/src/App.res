%%raw("import './App.css'")

type build = {id: string, result: string, count: int}
let columns = ["ID", "Result", "Count"]

let getData = () => {
  Js.Promise.make((~resolve, ~reject) =>
    resolve(. [
      {id: "test", result: "success", count: 42},
      {id: "test2", result: "failure", count: 1},
    ])
  )
}

let textTd = txt => <td> {txt->React.string} </td>

let intTd = i => <td> {i->string_of_int->React.string} </td>

module DataTable = {
  @react.component
  let make = (~columns, ~data) => {
    let mkColumnCell = column => <td> {column->React.string} </td>
    let columnCells = Belt.Array.map(columns, mkColumnCell)
    let mkRow = row => {
      let cells = [textTd(row.id), textTd(row.result), intTd(row.count)]
      <tr> {cells->React.array} </tr>
    }
    let rowCells = Belt.Array.map(data, mkRow)
    <>
      <h1> {"Table"->React.string} </h1>
      <table>
        <thead> <tr> {columnCells->React.array} </tr> </thead>
        <tbody> {rowCells->React.array} </tbody>
      </table>
    </>
  }
}

module App = {
  @react.component
  let make = () => {
    let (data, setData) = React.useState(() => [])

    React.useEffect0(() => {
      let void = getData() |> Js.Promise.then_(data => {
        Js.log2("got data", data)
        setData(_ => data)
        Js.Promise.resolve()
      })
      None // or Some(() => {})
    })

    <DataTable columns data />
  }
}

switch ReactDOM.querySelector("#root") {
| Some(root) => ReactDOM.render(<App />, root)
| None => ()
}
