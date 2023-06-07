import * as api from "../api/index";

export const getgooglecalendar = () => async(dispatch) => {
    try{
        const { data } = await api.getgooglecalendar();
        return data;
    }
    catch(error){
        return error.response.data[0];
    }
}

export const syncgooglecalendar = (syncedcalendar) => async(dispatch) => {
    try{
        console.log(syncedcalendar);
        const { data } = await api.syncgooglecalendar(syncedcalendar);
        return data;
    }
    catch(error){
        console.log(error);
    }
}