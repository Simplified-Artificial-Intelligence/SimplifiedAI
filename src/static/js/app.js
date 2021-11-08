Vue.component('v-date-time', {
    props: ['value'],

    template: `
      <div>
          <v-menu
              ref="menu"
              v-model="dropdownOpen"
              :close-on-content-click="false"
              :nudge-right="40"
              :return-value.sync="model"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              max-width="560px"
              min-width="560px">
              <template v-slot:activator="{ on }">
                  <v-text-field
                      v-model="displayDate"
                      label="Date Time"
                      prepend-icon="event"
                      readonly
                      v-on="on"
                  ></v-text-field>
              </template>

             <div class="v-date-time-widget-container">
                  <v-layout row wrap>
                      <v-flex xs12 sm6>
                          <v-date-picker
                              v-model="dateModel"
                              width="240"
                              color="primary"></v-date-picker>

                      </v-flex>
                      <v-flex xs12 sm6>
                          <v-btn small
                            fab
                            :color="meridiam === 'AM' ? 'primary' : 'darkgray'"
                            class="btn-am" @click="meridiam='AM'">AM</v-btn>

                          <v-btn
                                fab
                               small
                               :color="meridiam === 'PM' ? 'primary' : 'darkgray'"
                                class="btn-pm"
                                @click="meridiam='PM'">PM</v-btn>

                          <v-time-picker
                              v-if="dropdownOpen"
                              v-model="timeModel"
                              color="primary"
                              width="240"
                              :no-title="true"></v-time-picker>

                          <h3 class="text-xs-center">{{ currentSelection }}</h3>
                      </v-flex>

                      <v-flex xs12 class="text-xs-center">
                          <v-btn small @click="dropdownOpen = false" color="secondary">Cancel</v-btn>
                          <v-btn small @click="confirm()" color="primary">Ok</v-btn>
                      </v-flex>
                  </v-layout>
              </div>
          </v-menu>
      </div>
    `,

    data() {
      return {
        dropdownOpen: false,
        meridiam: 'AM',
        displayDate: '',
        dateModel: '',
        timeModel: '',
        monthNames: [
          "Jan", "Feb", "Mar",
          "Apr", "May", "June", "Jul",
          "Aug", "Sept", "Oct",
          "Nov", "Dec"
        ]
      }
    },

    computed: {
        model: {
            get() { return this.value; },
            set(model) {  }
        },

        currentSelection(){
            let selectedTime = this.timeModel+' '+this.meridiam
            return this.formatDate(this.dateModel) + ' '+selectedTime;
        }
    },

    methods: {
        formatDate(date) {
            if (!date) return '';

            const [year, month, day] = date.split('-')
            let monthName = this.monthNames[parseInt(month)]
            return `${monthName} ${day}, ${year}`;
        },

        // Confirm the datetime selection and close the popover
        confirm(){
            this.onUpdateDate();
            this.dropdownOpen = false
        },

        // Format the date and trigger the input event
        onUpdateDate(){
            if ( !this.dateModel || !this.timeModel) return false;

            let selectedTime = this.timeModel+' '+this.meridiam
            this.displayDate = this.formatDate(this.dateModel) + ' '+selectedTime
            this.$emit('input', this.dateModel + ' '+selectedTime);
        },
    },

    mounted(){
        // Set the current date and time as default value
        var d = new Date();
        var currentHour = d.getHours() % 12; // AM,PM format
        var minutes = (d.getMinutes() < 10 ? '0' : '') + d.getMinutes();
        var currentTime = currentHour+':'+minutes;
        this.timeModel = currentTime;
        this.dateModel = d.toISOString().substr(0, 10);

        if ( d.getHours() >= 12) {
          this.meridiam = 'PM';
        }
    }
});

const vm = new Vue({
  el: "#app",
  data(){
    return {
      myDateTime: 'Pick a Date'
    }
  }
});