<script>
export default {
  data() {
    return {
      api_server_base: "http://10.0.0.11/proxy_api",
      server_list: [],
      server_status: "UNKNOWN",
      listen_on: "UNKNOWN",
      server_started_time: "",
      running_config: "UNKNOWN",
      expiration_date: "UNKNOWN",
      remaining_traffic: "UNKNOWN",

      proxy_log: "",
      server_running_status_dict: {},  // map of true or false
    }
  },

  methods: {
    update_server_status_base() {
      fetch(this.api_server_base + "/get/proxy_info").then(
        resp => resp.json()
      ).then(
        data => {
          this.server_status = data.status
          this.remaining_traffic = data.remaining_traffic
          this.expiration_date = data.expiration_date
          this.listen_on = data.listen_on
          this.server_started_time = data.server_started_time
          for (var idx in this.server_list) {
            var server_name = this.server_list[idx]
            this.server_running_status_dict[server_name] = false
          }
          if (data.running_config == "__none__") {
            this.running_config = "none"
          } else {
            this.running_config = data.running_config

            // update status for group list
            this.server_running_status_dict[this.running_config] = true
          }

          this.get_proxy_log()
        }
      )
    },

    update_server_status() {
      if (this.server_list.length == 0) {
        this.get_server_list().then(() => {
          this.update_server_status_base()
        })
      } else {
        this.update_server_status_base()
      }
    },

    get_server_list() {
      return fetch(this.api_server_base + "/get/proxy_list").then(
        resp => resp.json()
      ).then(
        data => {
          this.server_list = data
          for (var idx in this.server_list) {
            var server_name = this.server_list[idx]
            this.server_running_status_dict[server_name] = false
          }
        }
      )
    },

    get_proxy_log() {
      fetch(this.api_server_base + "/get/proxy_log").then(
        resp => resp.json()
      ).then(
        data => {
          this.proxy_log = data.log
        }
      )
    },

    control_button_listener(event) {
      var element_id = event.target.id
      var button_action = element_id.split("_")[0]
      var proxy_name = element_id.split("_")[2]

      if ( button_action == "stop" && this.server_status == "running" ) {
        fetch(this.api_server_base + "/stop_proxy").then(
          resp => resp.json()
        ).then(
          data => {
            this.update_server_status()
            // this.get_proxy_log()
          }
        )
      } else if ( button_action == "start" && this.server_status == "stopped" ) {
        var url = new URL(this.api_server_base + "/start_proxy")
        url.search = new URLSearchParams({name: proxy_name})
        fetch(url).then(
          resp => resp.json()
        ).then(
          data => {
            this.update_server_status()
            // this.get_proxy_log()
          }
        )
      }
    },

    check_server_status(server_name) {
      if (server_name == self.running_config) {
        return "list-proxy-running"
      } else {
        return "list-proxy-stopped"
      }
    },

  },

  mounted() {
    // this.get_server_list()
    this.update_server_status()
  }
}
</script>

<template>
  <!-- proxy status -->
  <div class="card">
    <div class="card-header">
      <h4>Proxy Status</h4>
      <div class="r_button_container">
        <button @click="update_server_status">update status</button>
      </div>
    </div>

    <!-- <h5 class="text-center"></h5> -->
    <ul class="list-group list-group-flush">
      <li class="list-group-item" style="text-align:center; font-weight: bold;" :class="{'list-proxy-running': server_status == 'running'}">Server {{server_status}}</li>
      <li class="list-group-item">Proxy listen on: <span class="text-monospace">{{listen_on}}</span></li>
      <li class="list-group-item">Running config: <span class="text-monospace">{{running_config}}</span></li>
      <li class="list-group-item">Server started on: <span class="text-monospace">{{server_started_time}}</span></li>
      <li class="list-group-item">Remaining traffic: <span class="text-monospace">{{remaining_traffic}}</span></li>
      <li class="list-group-item">Expiration Date: <span class="text-monospace">{{expiration_date}}</span></li>
      <li class="list-group-item">API server address <input v-model="api_server_base" class="text-monospace" /></li>
    </ul>
  </div>
  <p>&nbsp;</p>

  <!-- proxy status -->
  <div class="card">
    <div class="card-header">
      <h4>Proxy List</h4>
    </div>
    <div class="list-group list-group-flush">
      <template v-for="server_name in server_list">
        <div class="list-group-item proxy-list-item" :id="'proxy_' + server_name" 
            :class="{'list-proxy-running': server_running_status_dict[server_name]}" >
          <button v-if=" !server_running_status_dict[server_name] "
            :id="'start_button_' + server_name" class="control-button"
            :class="{'control-button-disable': (server_status == 'running') && (!server_running_status_dict[server_name])}"
            @click="control_button_listener($event)"><i class="bi-play-fill"></i></button>
          <button v-else :id="'stop_button_' + server_name"
            class="control-button"  @click="control_button_listener($event)"><i class="bi-stop-fill"></i></button>
          &nbsp;
          {{server_name}}
        </div>
      </template>
    </div>
  </div>
  &nbsp;

  <!-- proxy log -->
  <div class="card">
    <div class="card-header">
      <h4>Proxy Log</h4>
      <div class="r_button_container">
        <button @click="get_proxy_log">update proxy log</button>
      </div>
    </div>
    <div class="card-text">
      <pre style="max-height: 500px;">{{proxy_log}}</pre>
    </div>
  </div>
  &nbsp;

  <!-- about -->
  <div class="card">
    <div class="card-header">
      <h4>About</h4>
    </div>
    <div class="card-text" style="text-align:center;">
      &nbsp;
      <p>By Andy. 2022.</p>
    </div>
  </div>
</template>

<style>
.proxy_info {
  margin: 10px;
}

.text-monospace { 
  font-family: monospace;
}

.r_button_container {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  padding: 10px;
}

.control-button {
  width: 60px;
  text-align: center;
  font-size: smaller;
  font-weight: bold;
}

.control-button-disable {
  color: rgb(181, 181, 181);
}

.list-proxy-running {
  background-color: #b7fdc9 !important;
}

</style>