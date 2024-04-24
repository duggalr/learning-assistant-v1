function generateUniqueUserID(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
    }
    return result;
};


// $('#signup-login-button').click(function(){

//     let new_url = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/login';
//     window.location.replace(new_url);

// });


// const initial_user_session = '{{ request.session }}';
// const anon_user_id = '{{ anon_user_id }}';

// console.log('user-stuff:', initial_user_session, anon_user_id);


