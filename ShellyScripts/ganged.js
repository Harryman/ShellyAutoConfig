let gang = "{{ gang_name }}";
let ids = {{ ganged_ids }};

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

MQTT.subscribe(Shelly.getComponentConfig("mqtt").topic_prefix +"/command/"+ gang, ganged);

