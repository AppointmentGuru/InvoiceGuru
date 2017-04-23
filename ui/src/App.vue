<template>
  <div id='app'>
    <h5>Sample Datas</h5>
    <div>
      <button
        v-for='data in datas'
        @click='setInvoice(data.data)' >{{data.name}}</button>
      <button
        @click='fromAppointments()' >From AppointmentGuru</button>
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
import {appointments} from './fakes/appointments'
import {practitioner} from './fakes/profile'

console.log(appointments)

export default {
  datas,
  appointments,
  practitioner,
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
    },
    fromAppointments () {
      let items = []
      for (let appointment of appointments) {
        let productLookup = {
          61: 'VusJS for Professionals',
          62: 'Building APIs with Python, Django and Django Rest Framework'
        }
        let item = {
          'name': `[${appointment.start_time}] consultation`,
          'quantity': 1,
          'unit_cost': appointment.price,
          'description': productLookup[appointment.product]
        }
        items.push(item)
      }
      let invoice = {
        'from': practitioner.results[0].first_name + ' ' + practitioner.results[0].last_name,
        'to': 'Tangent Solutions\nCulross Court, 16 Culross road, Bryanston, Johannesburg',
        'number': 'INV-2',
        'currency': 'ZAR',
        'date': '2017-04-25',
        'logo': 'http://placehold.it/350x150',
        'items': items,
        'notes': 'Can also: \ncontain multiple lines'
      }
      this.invoice = {
        name: 'AppointmentGuru example',
        data: invoice
      }
    }
  }
}
</script>
<style>
body {
  font-family: Roboto,'Helvetica Neue',Helvetica,Arial,sans-serif;
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
    font-family: 'Courier 10 Pitch', Courier, monospace;
    font-size: 95%;
    line-height: 140%;
    white-space: pre;
    white-space: pre-wrap;
    white-space: -moz-pre-wrap;
    white-space: -o-pre-wrap;
}

code {
    font-family: Monaco, Consolas, 'Andale Mono', 'DejaVu Sans Mono', monospace;
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
