<template>
  <div class="invoice-builder">
    <textarea v-model='invoice' style='width:400px;height:400px;' >
    </textarea>
    <div v-show='error' >{{error}}</div>
  </div>
</template>

<script>
export default {
  name: 'InvoiceBuilder',
  props: {
    value: { type: Object, required: true }
  },
  data () {
    return {
      invoice: JSON.stringify(this.value),
      error: false
    }
  },
  watch: {
    value () {
      this.invoice = JSON.stringify(this.value)
    },
    invoice () {
      let data = null
      try {
        data = JSON.parse(this.invoice)
        this.$emit('input', data)
        this.error = false
      } catch (err) {
        console.log(err)
        this.error = 'Not valid JSON'
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
