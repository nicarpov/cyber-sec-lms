let loading_alert = document.getElementById('loading-alert');
let start_alert = document.getElementById('start-alert');
let reboot_alert = document.getElementById('reboot-alert');
let start_btn = document.getElementById('start-btn');
let reboot_btn = document.getElementById('reboot-btn');
let back_btn = document.getElementById('back-btn');
let ready_alert = document.getElementById('ready-alert');
let reboot_eta_alert = document.getElementById('reboot-eta-alert')
// hideElements([loading_alert, start_alert, start_btn, back_btn])
let progress_bar = document.createElement('span');
loading_alert.appendChild(progress_bar)

socket.onmessage = function(event) {
    let jobState = JSON.parse(event.data);
    
    if(jobState){
        let status = jobState['status']
        if( status == 'ready'){
            hideElements([loading_alert])
            showElements([reboot_alert, reboot_btn ]);

        }else if(status == 'loading'){
            hideElements([ready_alert, back_btn, start_btn, reboot_alert])
            showElements([loading_alert]);
            
            
            progress_bar.innerHTML = bars[i];
            i++;
            if(i >= bars.length){
                i = 0
            }
                
        }else if(status == 'reboot'){
            hideElements([ready_alert, back_btn, start_btn, loading_alert, reboot_alert, reboot_btn]);
            showElements([reboot_eta_alert]);
        }else{
            showElements([start_alert, start_btn, back_btn])
        } 
  }};
          
// socket.onclose = function(event) {
// if (event.wasClean) {
//     alert(`[close] Соединение закрыто чисто, код=${event.code} причина=${event.reason}`);
// } else {
//     // например, сервер убил процесс или сеть недоступна
//     // обычно в этом случае event.code 1006
//     alert('[close] Соединение прервано');
// }
// };

// socket.onerror = function(error) {
// alert(`[error]`);
// };

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



