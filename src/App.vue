<template>
  <div id="app">
    <invoice-builder v-model='invoice' ></invoice-builder>
    <strong>Result:</strong>
    <pre>{{invoice}}</pre>
  </div>
</template>

<script>
import InvoiceBuilder from './components/InvoiceBuilder'
export default {
  name: 'app',
  components: { InvoiceBuilder },
  data () {
    return {
      invoice: {}
    }
  }
}
</script>
