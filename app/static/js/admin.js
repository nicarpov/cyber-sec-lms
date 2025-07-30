
hosts_sock.onmessage = function(event){
    state = JSON.parse(event.data)
    console.log(state['unregistered'])
}