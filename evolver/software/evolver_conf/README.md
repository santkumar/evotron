Follow these steps, once the default evolver platform is up and running: 

* ssh into the evolver raspberry pi
* Modify /home/pi/evolver/evolver/conf.yml file. Either replace the default file with this one or add the following lines into the default conf.yml file under "experimental_params"

opto_led1:

    fields_expected_incoming: 17
    
    fields_expected_outgoing: 17
    
    recurring: true
    
    value: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
