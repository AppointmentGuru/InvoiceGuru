<template>
  <div class="invoice-builder">
    <textarea v-model='invoice' >
    </textarea>
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
      invoice: JSON.stringify(this.value)
    }
  },
  watch: {
    invoice () {
      let data = null
      try {
        data = JSON.parse(this.invoice)
      } catch (err) {
        console.log(err)
        data = 'Not valid JSON'
      }
      this.$emit('input', data)
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
