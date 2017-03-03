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
    <br/><br>
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
        <el-table :data="value.data.items" style="width: 100%">
          <el-table-column prop="name" label="Item" width="300px">
            <template scope="scope">
              <el-input placeholder="Please input" v-model="scope.row.name"></el-input>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="Description" width="300px">
            <template scope="scope">
              <el-input placeholder="Please input" v-model="scope.row.description"></el-input>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="Quantity">
            <template scope="scope">
              <el-input placeholder="Please input" v-model="scope.row.quantity"></el-input>
            </template>
          </el-table-column>
          <el-table-column prop="unit_cost" label="Rate">
            <template scope="scope">
              <el-input placeholder="Please input" v-model="scope.row.unit_cost"></el-input>
            </template>
          </el-table-column>
          <el-table-column label="Amount">
            <template scope="scope">
              <span style="margin-left: 10px">{{ amount(scope.row.unit_cost, scope.row.quantity) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="">
            <template scope="scope">
              <el-button
              size="small"
              type="danger"
              @click="handleDelete(scope.$index, scope.row)">Delete</el-button>
            </template>
          </el-table-column>

        </el-table>
        <el-button type="primary" @click="handleCreate">Add line item</el-button>
      </el-col>
    </el-row>
    <br/><br/>
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
    },
    handleCreate (index, row) {
      this.value.data.items.push({
        name: null,
        quantity: 1,
        unit_cost: null,
        description: null
      })
    },
    handleDelete (index, row) {
      this.value.data.items.splice(index, 1)
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
<style>
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

th.is-leaf:first-child {
  border-top-left-radius: 10px;
  border-bottom-left-radius: 10px;
}

th.is-leaf:last-child {
  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;
}

th.is-leaf, th .cell {
  background-color: #000000 !important;
  color: #ffffff !important;
}

.el-table, .el-table::after, .el-table::before {
  border: none !important;
  margin-top: 60px;
  background-color: #fff !important;
}



</style>
