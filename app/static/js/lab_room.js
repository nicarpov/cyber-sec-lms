let loading_alert = document.getElementById('loading-alert');
let start_alert = document.getElementById('start-alert');
let start_btn = document.getElementById('start-btn');
let back_btn = document.getElementById('back-btn');
let ready_alert = document.getElementById('ready-alert');
// hideElements([loading_alert, start_alert, start_btn, back_btn])

socket.onmessage = function(event) {
    let jobState = JSON.parse(event.data);
    
    if(jobState){
        let status = jobState['status']
        if( status == 'ready'){
            hideElements([loading_alert])
            showElements([ready_alert, back_btn]);

        }else if(status == 'loading'){
            hideElements([ready_alert, back_btn, start_btn])
            showElements([loading_alert]);
        
    }else{
        showElements([start_alert, start_btn, back_btn])
    }
    
  }
  
};
          
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



