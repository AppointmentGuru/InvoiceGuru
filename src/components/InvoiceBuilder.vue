<template>
  <div class="invoice-builder">
    <el-row type="flex" :gutter="20" justify="space-between">
      <el-col :span="8">
        <img :src="value.data.logo" />
      </el-col>
      <el-col :span="4">
        <h2>INVOICE</h2> <br/>
      </el-col>
    </el-row>

    <el-row type="flex" :gutter="20" justify="space-between">
      <el-col :span="6">
        Bill To:
        <pre>{{value.data.to}}</pre>
      </el-col>
      <el-col :span="6">
        <table>
          <tbody>
            <tr>
              <td>Date:</td>
              <td>{{value.data.date}}</td>
            </tr>
            <tr>
              <td>Due Date:</td>
              <td>{{value.data.due_date}}</td>
            </tr>
            <tr>
              <td>Balance Due:</td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <div class="grid-content bg-purple">
          <el-table :data="value.data.items" stripe style="width: 100%">
            <el-table-column prop="name" label="Item"></el-table-column>
            <el-table-column prop="description" label="Description" width="300px"></el-table-column>
            <el-table-column prop="quantity" label="Quantity"></el-table-column>
            <el-table-column prop="unit_cost" label="Rate"></el-table-column>
            <el-table-column label="Amount">
            <template scope="scope">
              <span style="margin-left: 10px">{{ amount(scope.row.unit_cost, scope.row.quantity) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-col>
  </el-row>

  <textarea v-model='invoice' style='width:400px;height:400px;'></textarea>
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
  methods: {
    amount (cost, qty) {
      return parseFloat(cost) * parseFloat(qty)
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
