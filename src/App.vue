<template>
  <div id="app">
    <h1>InvoiceBuilder</h1>
    <h5>Sample Datas</h5>
    <div>
      <button
        v-for='data in datas'
        @click='setInvoice(data.data)' >{{data.name}}</button>
    </div>
    <hr/>
    <invoice-builder v-model='invoice' ></invoice-builder>
    <strong>Result:</strong>
    <pre>{{invoice}}</pre>
  </div>
</template>

<script>
import InvoiceBuilder from './components/InvoiceBuilder'
import {datas} from './mocks'

export default {
  datas,
  name: 'app',
  components: { InvoiceBuilder },
  data () {
    return {
      invoice: datas[0],
      datas: datas
    }
  },
  methods: {
    setInvoice (data) {
      this.invoice = data
    }
  }
}
</script>
<style>
body {
  font-family: Roboto,"Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size: 14px;
  font-weight: 400;
}
</style>
<style scoped>
#app {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

 pre {
    font-family: "Courier 10 Pitch", Courier, monospace;
    font-size: 95%;
    line-height: 140%;
    white-space: pre;
    white-space: pre-wrap;
    white-space: -moz-pre-wrap;
    white-space: -o-pre-wrap;
}

code {
    font-family: Monaco, Consolas, "Andale Mono", "DejaVu Sans Mono", monospace;
    font-size: 95%;
    line-height: 140%;
    white-space: pre;
    white-space: pre-wrap;
    white-space: -moz-pre-wrap;
    white-space: -o-pre-wrap;
    background: #faf8f0;
}

#content code {
    display: block;
    padding: 0.5em 1em;
    border: 1px solid #bebab0;
}
</style>
