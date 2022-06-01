import axios from 'axios';

export default setAuthToken => {
    if(token) {
        axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    }
    else{
        delete axios.defaults.headers.common['Authorization'];
    }
}