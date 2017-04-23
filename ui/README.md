# invoicebuilder

> An invoice generator using the Invoiced API: https://github.com/Invoiced/invoice-generator-api

**Usage**

```
<script>
let invoice = {
    'from': 'Joe Soap',
    'to': 'Jane Soap\nMust support multiple lines',
    'number': 'INV-123',
    'currency': 'ZAR',
    'date': today,
    'logo': 'http://placehold.it/350x150',
    'items': [
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
        },
    ],
    'notes': 'Can also: \ncontain multiple lines'
}
// more docs about what an invoice data looks like:
// https://github.com/Invoiced/invoice-generator-api
</script>

...

<invoice-builder v-model='invoice' ></invoice-builder>
```

**Building the docs/github page**

```
npm run build
# .. push to github
```

**Features**

- [ ] Display the invoice with the same look and feel of the generated invoice
- [ ] All values are editable (ideally as edit-in-place)
- [ ] ...


## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report

# run unit tests
npm run unit

# run e2e tests
npm run e2e

# run all tests
npm test
```

For detailed explanation on how things work, checkout the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).
