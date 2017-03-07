<template>
  <div class="invoice-builder">

    <!-- Logo and Document Title -->
    <el-row 
    type="flex"
    :gutter="20" 
    justify="space-between" >
    <el-col :span="8">
      <img :src="value.data.logo" />
    </el-col>
    <el-col :span="5">
      <h1>INVOICE</h1> <br/>
    </el-col>
  </el-row>

  <br/><br>

  <!--  Invoice Details -->
  <el-row 
  type="flex" 
  :gutter="20" 
  justify="space-between" >

  <!-- Address details -->
  <el-col :span="6">
    <span class="silver">Invoice From:</span> <br/><br/>
      <el-input 
      type="textarea" 
      :rows="2" 
      placeholder="Who is this invoice from?" 
      v-model="value.data.from">    
    </el-input>

  <br/>
  <span class="silver">Bill To:</span> <br/><br/>
    <el-input 
    type="textarea" 
    :rows="2" 
    placeholder="Who is this invoice to?" 
    v-model="value.data.to">    
  </el-input>

</el-col>

<!-- Dates -->
<el-col :span="6">
  <table width="100%">
    <tbody>
      <tr>
        <td><span class="silver">Date:</span></td>
        <td>
          <el-date-picker
          v-model="value.data.date"
          type="date"
          format="yyyy-MM-dd"
          placeholder="Pick a day">
        </el-date-picker>
      </td>
    </tr>
    <br/>
    <tr>
      <td><span class="silver">Due Date:</span></td>
      <td>
      <el-date-picker
        v-model="value.data.due_date"
        type="date"
        format="yyyy-MM-dd"
        placeholder="Pick a day">
      </el-date-picker>
      </td>
    </tr>
  </tbody>
</table>
</el-col>
</el-row>

<!--  Invoice line items -->
<el-row :gutter="20">
  <el-col :span="24">

    <el-table :data="value.data.items" style="width: 100%">

      <el-table-column prop="name" label="Item" width="300px">
        <template scope="scope">
          <el-input placeholder="Enter a product name" v-model="scope.row.name"></el-input>
        </template>
      </el-table-column>

      <el-table-column prop="description" label="Description" width="300px">
        <template scope="scope">
          <el-input placeholder="Enter a description" v-model="scope.row.description"></el-input>
        </template>
      </el-table-column>

      <el-table-column prop="quantity" label="Quantity">
        <template scope="scope">
          <el-input placeholder="Enter a quantity" v-model="scope.row.quantity"></el-input>
        </template>
      </el-table-column>

      <el-table-column prop="unit_cost" :label="unitCostLabel">
        <template scope="scope">
          <el-input placeholder="Enter a price" v-model="scope.row.unit_cost"></el-input>
        </template>
      </el-table-column>

      <el-table-column :label="amountLabel">
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

    <br/>

    <el-button type="primary" @click="handleCreate">Add line item</el-button>
  </el-col>
</el-row>

<br/><br/>

<span class="silver">Notes:</span>
<pre><el-input type="textarea" :rows="3" placeholder="Notes - any relevant information not covered" v-model="value.data.notes"></el-input></pre>

<br/><br/>

<span class="silver">Terms:</span>
<pre><el-input type="textarea" :rows="3" placeholder="Terms and conditions - late fees, payment methods, delivery schedule" v-model="value.data.terms"></el-input></pre>

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
        quantity: 0,
        unit_cost: 0,
        description: null
      })
    },
    handleDelete (index, row) {
      this.value.data.items.splice(index, 1)
    }
  },
  computed: {
    unitCostLabel () {
      return `Unit Cost ( ${this.value.data.currency} )`
    },
    amountLabel () {
      return `Amount ( ${this.value.data.currency} )`
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
  font-weight: bold;
  font-size: 50px;
  text-align: left;
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
tbody .cell {
  padding: 10px 5px !important;
}
.el-textarea {
  display: block !important;
}
.silver{
  color: #8492A6;
}
</style>
