var fetchData = {
    labs: [],
    reservations: [],
    states: []
}

var filteredData = {
    labs: [],
    reservations: [],
    states: []
}

function fetchTheData() {
    fetchData = {
        labs: [],
        reservations: [],
        states: []
    }
    fetch('http://localhost:8000/labs')
        .then(res => {
            return res.json();
        })
        .then(res => {
            res._items.forEach(item => {
                lab = {
                    lab_ID: item._id,
                    lab_NAME: item.lab_name,
                    lab_TYPE: item.lab_type,
                    lab_STATUS: item.status,
                    lab_RESERVATION: "",
                    lab_RESERVATION_STATUS: "",
                    lab_SEARCH_TERM: ""
                };
                if (item.hasOwnProperty('reservation') && item.reservation != null) {
                    lab.lab_RESERVATION = item.reservation;
                    lab.lab_RESERVATION_STATUS = "RESERVED";
                } else {
                    lab.lab_RESERVATION = "none";
                    lab.lab_RESERVATION_STATUS = "FREE";
                }
                lab.lab_SEARCH_TERM += (lab.lab_RESERVATION_STATUS + lab.lab_NAME + lab.lab_TYPE + lab.lab_STATUS);
                fetchData.labs.push(lab);
            });
        })
        .then(() => {
            return fetch('http:/localhost:8000/reservations');
        })
        .then(res => {
            return res.json();
        })
        .then(res => {
            res._items.forEach(item => {
                reservation = {
                    res_ID: item._id,
                    res_LAB_ID: item.lab,
                    res_USERNAME: item.username,
                    res_MESSAGE: "",
                    res_ETAG: item._etag
                };
                if (item.hasOwnProperty('message')) {
                    reservation.res_MESSAGE = item.message;
                } else {
                    reservation.res_MESSAGE = "No message";
                }
                fetchData.reservations.push(reservation);
            });
        })
        .then(() => {
            return fetch('http:/localhost:8000/states');
        })
        .then(res => {
            return res.json();
        })
        .then(res => {
            res._items.forEach(item => {
                state = {
                    state_ID: item._id,
                    state_LAB_ID: item.lab,
                    state_BUILD_ID: item.build.id,
                    state_SNAPSHOT_ID: item.snapshot_id,
                    state_SNAPSHOT_STATUS: item.snapshot_status,
                    state_UPDATED: item._updated,
                    state_ETAG: item._etag
                };
                if(item.hasOwnProperty('admin_server_access')) {
                    state.state_ADMIN_SERVER_ACCESS = item.admin_server_access;
                } else {
                    state.state_ADMIN_SERVER_ACCESS = {
                        username: "",
                        host: "",
                        password: "",
                        port: 0
                    }
                }
                fetchData.states.push(state);
            });
        })
        .then(() => {
            appendData(fetchData);
        })
        .then(() => {
            initGraphs();
        })
        .then(() => {
            removeLoader();
        })
        .then(() => {
            initEventListeners();
        })
        .catch(err => {
            console.log("error :(");
            console.log(err);
        });
}


function appendData(data) {
    let counter = 0;
    let stateCounter = 0;
    data.labs.forEach(lab => {
        
        let labHTML, stateHTML, newLabHTML, newStateHTML;
        let res_name, res_msg;
        let labStates = "";
        labHTML = `<div class="card card-top lab-card">
        <div class="card-header lab-test" role="tab" data-toggle="collapse" href="#collapse-${counter}" id="heading-${counter}">
            <div class="row">
                <h5 class="mb-0 col-md-11">
                    <a class="row link-center" aria-expanded="true" aria-controls="collapse-${counter}">
                        <span class="lab-res-stat col-md-2 col-sm-6">${lab.lab_RESERVATION_STATUS}</span>
                        <span class="lab-name col-md-2 col-sm-6">${lab.lab_NAME}</span>
                        <span class="lab-type col-md 2 col-sm-6">${lab.lab_TYPE}</span>
                        <span class="lab-stat col-md-3 col-sm-6">${lab.lab_STATUS}</span>
                        <span class="lab-reserved-by col-md-2 col-sm-6">%res-name%</span>
                    </a>
                </h5>
                <button type="button" id="btn-${counter}" class="btn btn-%btn-color%" onclick="displayModal(event)" data-toggle="modal" data-target="#modal">%res-status%</button>
            </div>
        </div>
    
        <div id="collapse-${counter}" class="collapse" role="tabpanel" aria-labelledby="heading-${counter}" data-parent="#accordion">
            <div class="card-body lab-test">
                <p class="lab-reservation-msg">%res-msg%</p>
                <div id="accordion2" role="tablist">%snapshot%</div>
            </div>
        </div>`;
        stateHTML = `<div class="card state-card">
                    <div class="card-header state-header" role="tab" id="">
                        <h5 class="row">
                            <a class="col-md-8" data-toggle="collapse" href="#state-collapse-%state-counter%" aria-expanded="true" aria-controls="state-collapse-%state-counter%">
                                <span class="lab-name">Snapshot build id: %build-id%</span>
                            </a>
                            <div class="col-md-4 text-right" >
                                <button class="btn btn-outline-info" onclick="displayStatePatchModal(event)" data-toggle="modal" data-target="#modal">Admin server access</btn>
                            </div>
                    </h5>
                    </div>
                    <div id="state-collapse-%state-counter%" class="collapse state-body" role="tabpanel" aria-labelledby="heading-%state-counter%" data-parent="#accordion2">
                        <div class="card-body row snaprow state-body-content">
                            <p class="col-md-3">Snapshot ID</p>
                            <p class="col-md-3">State ID</p>
                            <p class="col-md-3">Status</p>
                            <p class="col-md-3">Updated</p> 
                        </div>
                        <div class="card-body row state-body-content">
                            <p class="state-snapshot-id col-md-3">%snapshot-id%</p>
                            <p class="state-_id col-md-3">%state-id%</p>
                            <p class="state-snapshot-status col-md-3">%snapshot-status%</p>
                            <p class="state-build-history col-md-3">%build-updated%</p>
                        </div>
                    </div>
                </div>`;

                

        // Set reservation related data depending on iterated lab status
        if (lab.lab_RESERVATION_STATUS === "FREE") {
            newLabHTML = labHTML.replace('%res-name%', "");
            newLabHTML = newLabHTML.replace('%res-msg%', "");
            newLabHTML = newLabHTML.replace('%res-status%', "Reserve");
            newLabHTML = newLabHTML.replace('%btn-color%', "primary");
        } else if (lab.lab_RESERVATION_STATUS === "RESERVED") {
            fetchData.reservations.forEach(r => {
                if (r.res_ID === lab.lab_RESERVATION) {
                    res_name = r.res_USERNAME;
                    res_msg = r.res_MESSAGE;
                    fetchData.labs[
                        fetchData.labs.findIndex((lab) => {
                            return lab.lab_RESERVATION == r.res_ID;
                        })
                    ].lab_SEARCH_TERM += res_name;

                }
            });
            newLabHTML = labHTML.replace('%res-name%', res_name);
            newLabHTML = newLabHTML.replace('%res-msg%', res_msg);
            newLabHTML = newLabHTML.replace('%res-status%', "Release");
            newLabHTML = newLabHTML.replace('%btn-color%', "danger");
        }

        // Add snapshots to current lab iteration
        let firstSnap = true;

        // At this point I should have whole searchterm - states
        data.states.forEach(s => {
            if (s.state_LAB_ID == lab.lab_ID) {
                let stateBuildId = s.state_BUILD_ID;
                let stateUpdated = s.state_UPDATED;
                // TODO insert itegrated NES here
                let stateSnapshotId = s.state_SNAPSHOT_ID;
                let stateSnapStatus = s.state_SNAPSHOT_STATUS;
                let stateId = s.state_ID;

                // replace statements
                newStateHTML = stateHTML.replace('%build-id%', stateBuildId);
                newStateHTML = newStateHTML.replace('%build-updated%', stateUpdated);
                newStateHTML = newStateHTML.replace('%snapshot-id%', stateSnapshotId);
                newStateHTML = newStateHTML.replace('%state-id%', stateId);
                newStateHTML = newStateHTML.replace('%snapshot-status%', stateSnapStatus);
                do {
                    newStateHTML = newStateHTML.replace('%state-counter%', stateCounter);
                } while (newStateHTML.includes('%state-counter%'));

                fetchData.labs[
                    fetchData.labs.findIndex((lab) => {
                        return lab.lab_ID == s.state_LAB_ID;
                    })
                ].lab_SEARCH_TERM += stateBuildId;

                // Add state to iterated labs labstates string
                labStates += newStateHTML;
                stateCounter++;
            }
        });
        newLabHTML = newLabHTML.replace('%snapshot%', labStates);
        document.getElementById("accordion").insertAdjacentHTML('beforeend', newLabHTML);
        counter++;
        
    });
    //Set colorcoding after appending the data
    reservationColor();
}


//Removes the loader after everything is loaded
function removeLoader() {
    if(document.getElementById("loader") !== null) {
        document.getElementById("loader").remove();
    } 
}


function initGraphs() {
    
    //Get the amount of reservated labs and display the info in a piechart
    var reservations = 0;

    fetchData.labs.forEach((lab) => {
        if (lab.lab_RESERVATION_STATUS === "RESERVED") {
            reservations++;
        }
    });

    var ctx = document.getElementById("chart-container-1").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            datasets: [{
                data: [reservations, fetchData.labs.length - reservations],
                backgroundColor: [
                    '#4ae83c',
                    '#236ace'
                    
                ]
            }],
            labels: [
                'Reserved: ' + reservations,
                'Free: ' + (fetchData.labs.length - reservations)
            ]
        },
        options: {
            legend: {
                position: "right"
            },
            title: {
                display: true,
                posion: "top",
                text: "Lab reservation status"
            },
            rotation: 180
        }
    });


    var ctx2 = document.getElementById("chart-container-2").getContext('2d');
    var myChart2 = new Chart(ctx2, {
        type: 'pie',
        data: {
            datasets: [{
                data: [getNoLabs("sprint"), getNoLabs("cloud"), getNoLabs("vsprint"), getNoLabs("other")],
                backgroundColor: [
                    '#4ee086',
                    '#2fe9ed',
                    '#ed5c4b',
                    '#6f60d1'
                ]
            }],
            labels: [
                'Sprint: ' + getNoLabs("sprint"),
                'Cloud: ' + getNoLabs("cloud"),
                'VSprint: ' + getNoLabs("vsprint"),
                'Other: ' + getNoLabs("other")
            ]
        },
        options: {
            legend: {
                position: "right"
            },
            title: {
                display: true,
                posion: "top",
                text: "Lab types"
            },
            rotation: 200
        }
    });

    var ctx3 = document.getElementById("chart-container-3").getContext('2d');
    var myChart3 = new Chart(ctx3, {
        type: 'pie',
        data: {
            datasets: [{
                data: [
                    getNoStatuses("ready"),
                    getNoStatuses("initializing"),
                    getNoStatuses("queud_for_initialization"),
                    getNoStatuses("queud_for_revert"),
                    getNoStatuses("reverting_state"),
                    getNoStatuses("state_operation_failed")
                ],
                backgroundColor: [
                    '#4ae83c',
                    '#236ace',
                    '#08cbd6',
                    '#cdd102',
                    '#f18a03',
                    '#ed0909'
                ]
            }],
            labels: [
                "Ready: " + getNoStatuses("ready"),
                "Initializing: " + getNoStatuses("initializing"),
                "queud_for_initialization: " + getNoStatuses("queud_for_initialization"),
                "queud_for_revert: " + getNoStatuses("queud_for_revert"),
                "reverting_state: " + getNoStatuses("reverting_state"),
                "state_operation_failed: " + getNoStatuses("state_operation_failed")
            ]
        },
        options: {
            legend: {
                position: "right"
            },
            title: {
                display: true,
                posion: "top",
                text: "Lab statuses"
            },
            rotation: 100
        }

    });
    document.getElementById("number-of-labs").innerHTML = fetchData.labs.length;
}

//Helper function that returns the amount of labs in a certain state
function getNoStatuses(state) {
    var counter = 0;
    fetchData.labs.forEach((lab) => {
        if (lab.lab_STATUS === state) {
            counter++;
        }
    });
    return counter;
}

//Helper function that returns the amount of certain type of labss
function getNoLabs(type) {
    var counter = 0;
    fetchData.labs.forEach((lab) => {
        if (lab.lab_TYPE === type) {
            counter++;
        }
    });
    return counter;
}

//Color code cards
function reservationColor() {
    var cards = document.querySelector("#accordion").querySelectorAll('.card-top');

    cards.forEach((event) => {
        if (event.querySelector(".lab-stat").innerHTML == "ready") {

            event.querySelector(".card-header").style = "background-color: #cffcc2";
        } else if (event.querySelector(".lab-stat").innerHTML == "state_operation_failed") {

            event.querySelector(".card-header").style = "background-color: #ff7856";
        } else if (event.querySelector(".lab-stat").innerHTML == "reverting_state") {
            event.querySelector(".card-header").style = "background-color: #f9f5bd";
        } else if (event.querySelector(".lab-stat").innerHTML == "queued_for_initialization") {
            event.querySelector(".card-header").style = "background-color: #ead08f"; 
        }
    });
}

//Toggle graphs between visible and hidden
function toggleGraphs() {
    var e = document.querySelector("#graph-container");

    if (e.style.display === "none") {
        e.style.display = "block";
    } else {
        e.style.display = "none";
    }
}

//Add event listener to the search bar
function initEventListeners() {
    document.getElementById("search-bar").addEventListener("input", _.debounce(filterData, 300));

    //Enable tooltips in bootstrap 4
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
}



function displayModal(event) {
    if(document.getElementById("accordion").querySelector("#modal") != null) {
        document.getElementById("modal").parentNode.removeChild(document.getElementById("modal"));
    }
    let labName = event.target.parentElement.children[0].children[0].children[1].innerHTML;

    var modal = `<div class="modal fade" id="modal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title" id="modalLabel">${labName}</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
        <div class="modal-body">
            Are you sure you wish to ${event.target.innerHTML} "${labName}"?
            %msg%
        </div>
        <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
        <button type="button" class="%class%" onclick="processReservationAction(event)" data-dismiss="modal">${event.target.innerHTML}</button>
    </div>
    </div>
</div>
</div>`;


    if(event.target.innerHTML === "Reserve") {
        modal = modal.replace("%class%", "btn btn-success");
        modal = modal.replace("%msg%", "<input id='res-msg' class='form-control' placeholder='Reservation message' aria-label='Reservation message' required>");
    } else {
        modal = modal.replace("%class%", "btn btn-danger");
        modal = modal.replace("%msg%", "");
        
    }
    document.getElementById("accordion").insertAdjacentHTML('beforeend', modal);
}

function displayStatePatchModal(event) {
    if(document.getElementById("accordion").querySelector("#modal") != null) {
        document.getElementById("modal").parentNode.removeChild(document.getElementById("modal"));
    }
    let currentBuildIdHTML = event.target.parentElement.parentElement.querySelector('.lab-name').innerHTML.split(": ");
    let buildId = currentBuildIdHTML[1];
    
    // Using buildId we can loop over states to find correct one
    // returns first element that matches argument
    let curState = fetchData.states.find((state) => {
        return state.state_BUILD_ID === buildId;
    });

    var modal = `
    <div class="modal fade show" id="modal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
        <div class="modal-header">
            <div class="container">
                <div class="row">
                    <h5 class="modal-title" id="modalLabel">Update admin server access</h5>
                </div>
                <div class="row">
                    <h5 class="modal-title buildID" id="modalLabel">%snapshot_build_id%</h5>
                </div>
            </div>
        </div>    
        <div class="modal-body">
            
            <form>
                <div class="form-group">
                <label for="username">Username</label>
                <input type="text" class="form-control" id="username" value="%username%">
                </div>
                <div class="form-group">
                    <label for="host">Host</label>
                    <input type="text" class="form-control" id="host" value="%host%">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" class="form-control" id="password" value="%password%">
                </div>
                <div class="form-group">
                    <input type="checkbox" onclick="togglePassword()"> Show Password
                </div>
                <div class="form-group">
                    <label for="port">Port</label>
                    <input type="text" class="form-control" id="port" value="%port%">
                </div>
            </form>
        </div>
        <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-warning" onclick="processPatchAction(event)" data-dismiss="modal">Update</button>
    </div>
    </div>
</div>
</div>`;
    modal = modal.replace("%snapshot_build_id%", buildId);
    modal = modal.replace("%username%", curState.state_ADMIN_SERVER_ACCESS.username);
    modal = modal.replace("%host%", curState.state_ADMIN_SERVER_ACCESS.host);
    modal = modal.replace("%password%", curState.state_ADMIN_SERVER_ACCESS.password);
    modal = modal.replace("%port%", curState.state_ADMIN_SERVER_ACCESS.port);
    
    document.getElementById("accordion").insertAdjacentHTML('beforeend', modal);
}

function createLabModal() {
    if(document.getElementById("accordion").querySelector("#modal") != null) {
        document.getElementById("modal").parentNode.removeChild(document.getElementById("modal"));
    }
    

    var modal = `
    <div class="modal fade show" id="modal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalLabel">Create a lab</h5>
                </div>
            <div class="modal-body">
                <form id="newLabForm" action="http://localhost:8000/labs" enctype="application/json" method="POST">
                    <div class="form-group">
                        <label for="lab-name">Username</label>
                        <input type="text" class="form-control" id="lab-name" name="lab_name" placeholder="lab name" value="Testilabra">
                    </div>
                    <div class="form-group">
                        <label for="exampleFormControlSelect1">Example select</label>
                        <select class="form-control" name="lab_type" id="exampleFormControlSelect1">
                            <option value="sprint">sprint</option>
                            <option value="vsprint">vsprint</option>
                            <option value="cloud">cloud</option>
                            <option value="other">other</option>
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onClick="submitForm(document.getElementById('newLabForm'))" data-dismiss="modal">Create</button>
                    </div>
                </form>
            </div>  
        </div>
    </div>
</div>`;

        
    document.getElementById("accordion").insertAdjacentHTML('beforeend', modal);
}

function submitForm(form) {
    let url = "http://localhost:8000/labs"
    let labName = form.querySelector("#lab-name").value;
    let labType = form.querySelector("#exampleFormControlSelect1").value;
    
    var headers = new Headers({
        "accept": "application/json",
        "Content-type": "application/json"
    });

    let params = {
        "method": "post",
        "headers": headers,
        "body": JSON.stringify({
            "lab_name": labName,
            "lab_type": labType
        })   
    };

    fetch(url, params)
    .then(function(res) {
        location.reload(true);        
    });
}

//Filter the showed data with search terms
function filterData() {
    var searchTerms = document.getElementById("search-bar").value.split(' ');
    filteredData.labs = [];
    filteredData.states = [];
    fetchData.labs.forEach(lab => {
        var constainsSearchItem = true;
        //debugger;
        for(var term in searchTerms) {
            if(!lab.lab_SEARCH_TERM.toLowerCase().includes(searchTerms[term].toLowerCase())) {
                constainsSearchItem = false;
            }
        }
        if(constainsSearchItem) {
            filteredData.labs.push(lab);
        }
    });
    filteredData.labs.forEach(lab => {
        fetchData.reservations.forEach(res => {
            if(res.res_LAB_ID === lab.lab_ID) {
                filteredData.reservations.push(res);
            }
        });
        fetchData.states.forEach(state => {
            if(state.state_LAB_ID === lab.lab_ID) {
                filteredData.states.push(state);
            }
        });
    });
    document.getElementById("accordion").innerHTML = "";
    appendData(filteredData);
}

fetchTheData();

function processPatchAction(event) {
    console.log("Patch");
    let b_id;
    let state;
    let state_id;
    let url;
    let headers;
    let patchParams;

    var setupPatchPromise = new Promise((resolve, reject) => {
        console.log("First");
        b_id = document.querySelector(".buildID").innerHTML;
        
        state = fetchData.states.find((state) => {
            return state.state_BUILD_ID === b_id;
        });
        
        if(state !== undefined) {
            resolve("Stuff worked again!");
        } else {
            reject("Stuff broke again");
        }
    });

    var patchPromise = new Promise((resolve, reject) => {
        url = "http://localhost:8000/states/" + state.state_ID;
        console.log("second");
        headers = new Headers({
            "If-Match": state.state_ETAG,
            "accept": "application/json",
            "Content-type": "application/json"
        });
    
        patchParams = { 
            "method": "PATCH",
            "headers": headers,
            "body": JSON.stringify({
                "lab": state.state_LAB_ID,
                "build": {
                    "id": b_id
                },
                "admin_server_access": {
                    "username": document.getElementById("username").value,
                    "host": document.getElementById("host").value,
                    "password": document.getElementById("password").value,
                    "port": document.getElementById("port").value
                }
            })
        };
        if (patchParams != undefined) {
            resolve("Stuff worked!");
        }
        else {
            reject(Error("It broke"));
        }
    });
    
    setupPatchPromise.then((setupResult) => {
        patchPromise.then(function(patchResult) {

            fetch(url, patchParams)
            .then(function(res) {
                location.reload(true);                
            });

        }, function(err) {
        console.log(err); // Error: "It broke"
        });
    });
}


function processReservationAction(event) {

    var reservationAction = event.target.innerHTML;
    var labName = document.getElementById("modalLabel").innerHTML;
    var lab_ID;
    var res_ID;
    var res_ETAG;

    var postParams;
    var data;

    var url = "http://localhost:8000/reservations";

    var headers = new Headers({
        "accept": "application/json",
        "Content-type": "application/json"
    });

    var promise1 = new Promise((resolve, reject)=>{
        fetchData.labs.forEach((lab)=>{
            if(lab.lab_NAME == labName) {
                lab_ID = lab.lab_ID;
            }
        });
        fetchData.reservations.forEach(reservation => {
            if(reservation.res_LAB_ID == lab_ID) {
                res_ID = reservation.res_ID;
                res_ETAG = reservation.res_ETAG;
            }
        });
        if(lab_ID !== undefined) {
            resolve("Stuff worked again!");
        } else {
            reject("Stuff broke again");
        }
    });


    var promise = new Promise(function(resolve, reject) {
        
        if(reservationAction === "Release") {
            postParams = { 
                "method": "DELETE",
                "headers": new Headers({
                    "If-Match": res_ETAG
                }),
                "body": JSON.stringify({
                    "reservationID": res_ID,
                })
            };
            url += "/" + res_ID;
        } else {
            var res_MSG = document.getElementById("res-msg").value;
            postParams = {
                "method": "post",
                "headers": headers,
                "body": JSON.stringify({
                    "username": "Admin",
                    "message": res_MSG,
                    //"_id": "string",
                    //"expireAt": "2017-11-17T15:42:00",
                    "lab": lab_ID
                })   
            };
        }
        data = postParams;

        if (postParams != undefined) {
          resolve("Stuff worked!");
        }
        else {
          reject(Error("It broke"));
        }
      });
      
      promise1.then((result1)=>{
        console.log(result1);
    
      promise.then(function(result) {
        console.log(result);

        fetch(url, data)
        .then(function(res) {
            location.reload(true);

            
        });
      }, function(err) {
        console.log(err); // Error: "It broke"
      });
    });
    
}


function togglePassword() {
    var x = document.getElementById("password") 

    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}
