let gang = '{{ gang_name }}';
let ids = {{ ganged_ids }};

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

Shelly.addStatusHandler(printStatus);