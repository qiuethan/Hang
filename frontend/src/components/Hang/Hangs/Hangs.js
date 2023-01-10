import React, { useEffect } from 'react';
import {useDispatch, useSelector} from 'react-redux';

import { gethangevents } from '../../../actions/hang';

import Hang from './Hang/Hang';

const Hangs = () => {

    const dispatch = useDispatch();

    const hangs = useSelector((state) => state.hangs);
    console.log(hangs);

    useEffect(() => {
        dispatch(gethangevents());
    }, [])



    return(
        <div>
            {hangs.map((hang) => (
                <Hang key={hang.id} props={hang}/>
            ))}
        </div>
    )
}

export default Hangs;