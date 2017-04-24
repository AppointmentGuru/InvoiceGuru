// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import { Row, Col, Table, TableColumn, Button, Input, DatePicker, Upload, Message, MessageBox, Notification } from 'element-ui'
import 'element-ui/lib/theme-default/index.css'

Vue.component(Row.name, Row)
Vue.component(Col.name, Col)
Vue.component(Table.name, Table)
Vue.component(TableColumn.name, TableColumn)
Vue.component(Button.name, Button)
Vue.component(Input.name, Input)
Vue.component(DatePicker.name, DatePicker)
Vue.component(Upload.name, Upload)
Vue.component(Message.name, Message)
Vue.component(MessageBox.name, MessageBox)
Vue.component(Notification.name, Notification)

Vue.config.productionTip = false

Vue.prototype.$notify = Notification
Vue.prototype.$message = Message

/* eslint-disable no-new */
new Vue({
  el: '#app',
  template: '<App/>',
  components: { App }
})
