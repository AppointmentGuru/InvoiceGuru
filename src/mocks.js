/* eslint quotes: ["error", "double"] */
const SIMPLE_INVOICE = {
  "from": "Joe Soap",
  "to": "Jane Soap\nMust support multiple lines",
  "number": "INV-123",
  "currency": "ZAR",
  "date": "2017-02-28",
  "logo": "http://placehold.it/350x150",
  "items": [
    {
      "name": "Some lineitem",
      "quantity": 1,
      "unit_cost": 100,
      "description": "more information about some lineitem"
    },
    {
      "name": "Some other lineitem",
      "quantity": 2,
      "unit_cost": 200
    }
  ],
  "notes": "Can also: \ncontain multiple lines"
}

const NO_LINEITEMS_INVOICE = {
  "from": "Joe Soap",
  "to": "Jane SoapMust support multiple lines",
  "number": "INV-123",
  "currency": "ZAR",
  "date": "2017-02-28",
  "logo": "http://placehold.it/350x150",
  "items": [],
  "notes": "Can also: contain multiple lines"
}

export const datas = [
  {name: "Simple Invoice", data: SIMPLE_INVOICE},
  {name: "No limeitems", data: NO_LINEITEMS_INVOICE}
]
