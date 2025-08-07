let loading_alert = document.getElementById('loading-alert');
let reboot_alert = document.getElementById('reboot-alert');
let ready_alert = document.getElementById('ready-alert');
let reboot_eta_alert = document.getElementById('reboot-eta-alert')
let alerts = [loading_alert, reboot_alert, ready_alert, reboot_eta_alert]
let ready_message = document.getElementById('ready-message')

socket.onmessage = function(event) {
    let jobState = JSON.parse(event.data);
    // console.log(jobState)
    if(jobState){
        let status = jobState['status']
        
        if( status == 'ready'){
            hideElements(alerts)
            if (jobState["job_type"] == 'save'){
                showElements([ready_alert])
                ready_message.textContent = 'Состояние успешно сохранено!'
            }else if(jobState["job_type"] == 'load'){
                showElements([reboot_alert ]);
                ready_message.textContent = 'Состояние успешно загружено!'
            }
            
        

        }else if(status == 'loading'){
            hideElements(alerts)
            showElements([loading_alert])
                
        }else if(status == 'reboot'){
            hideElements(alerts)
            showElements([reboot_eta_alert])
        }else{

        } 
  }else{
    hideElements(alerts)
  }};
          

function hideElements(elements){
    for (let el of elements){
        el.classList.add('hidden');
    }
}

function showElements(elements){
    for (let el of elements){
        el.classList.remove('hidden');
    }
}