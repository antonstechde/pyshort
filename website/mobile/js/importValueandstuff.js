function getUrls(){
    link2short = encodeURIComponent(document.getElementById("link2short").value);
    customLink = document.getElementById("customlink2").value.replace(/\s+/g, '')

    if (customLink.trim() ===""){
        fetch(`https://api.pyshort.de?points_to=${link2short}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                doThingWithResults(data);
            })
    }
    else{
        fetch(`https://api.pyshort.de?short=${customLink}&points_to=${link2short}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                doThingWithResults(data);
            })
    }

    document.getElementById("createshortbutton").disabled = true;

}

function doThingWithResults(data) {
    const span = document.querySelector('#apiresponse');
    span.innerText = `${data}`
}



