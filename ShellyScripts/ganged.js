let gang = "{{ gang_name }}";
let ids = {{ ganged_ids }};

//function to turn on or off all devices in the gang
function ganged(topic,message){
    if(message === "on"){
        for(i in ids){
            Shelly.call("Switch.set", {'id': ids[i], 'on': true});
        }
    }
    else{
        for(i in ids){
            Shelly.call("Switch.set", {'id': ids[i], 'on': false});
        };
    }
};

//adding function
function printStatus(status) {
    let out = {
        apower: 0,
        voltage: 0,
        current: 0,
        pf: 0,
        aenergy: {total: 0},
        ret_aenergy: {total: 0},
        temperature: {tC: 0}
    };

    if (status.name === "switch" && status.id === ids[0]) {
        for (let i = 0; i < ids.length; i++) {
            let id = Shelly.getComponentStatus("switch", ids[i]);
            out.apower += id.apower;
            out.voltage += id.voltage;
            out.current += id.current;
            out.pf += id.pf;
            out.aenergy.total += id.aenergy.total;
            out.ret_aenergy.total += id.ret_aenergy.total;
            out.temperature.tC += id.temperature.tC;
        }
        let len = ids.length;
        out.voltage /= len;
        out.pf /= len;
        out.temperature.tC /= len;
        MQTT.publish(Shelly.getComponentConfig('mqtt').topic_prefix +'/status/'+ gang, JSON.stringify(out), 0,true)
    }
}


//subscribing to the topic
MQTT.subscribe(Shelly.getComponentConfig("mqtt").topic_prefix +"/command/"+ gang, ganged);
//adding the status handler to kick off addition and publishing
Shelly.addStatusHandler(printStatus);