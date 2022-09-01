<template>
  <div class="container">
  <center>
    <div class="row">
      <div class="col-sm-10">
        <h1>TF-IDF<sup>2</sup></h1>
        <br><br>
        <input v-on:input="update">
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col" style="width: 400px;">URL</th>
              <th scope="col" style="width: 500px;">Abstract</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(result, index) in defaults" :key="index">
              <td style="width: 400px;"><a :href='result.url'>{{ result.url }}</a></td>
              <td style="width: 500px;">{{ result.abstract }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </center>
  </div>
</template>

<style>
    input{
        outline-style: none ;
        border: 1px solid #ccc;
        border-radius: 3px;
        padding: 6px;
        width: 300px;
        font-size: 14px;
    }
    input:focus{
        border-color: #66afe9;
        outline: 0;
        -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgba(102,175,233,.6);
        box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgba(102,175,233,.6)
    }
    .row{
        display: contents !important;
        align-content: center;
    }
    .table td{
        vertical-align: middle;
        /* border-top: 0px solid #dee2e6;
        border-bottom: 0px solid #dee2e6;*/
    }
    .table thead td{
        text-align: center;
        /* border-top: 0px solid #dee2e6;
        border-bottom: 0px solid #dee2e6;*/
    }
    .table thead th{
        text-align: center;
        /* border-top: 0px solid #dee2e6;
        border-bottom: 0px solid #dee2e6;*/
    }
    .table{
        table-layout: fixed;
        overflow-wrap: anywhere;
    }
    .col-sm-10 {
        /* background: #1ABC9C; */
        border-radius: 6px;
    }
</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      defaults: [],
    };
  },
  methods: {
    update(payload) {
      const path = 'http://127.0.0.1:5000/query';
      // this.defaults = [{ 'url': '', 'abstract': payload.target.value }];
      axios.post(path, payload.target.value)
        .then((res) => {
          this.defaults = res.data.defaults;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.getBooks();
        });
    },
  },
  created() {
  },
};
</script>
