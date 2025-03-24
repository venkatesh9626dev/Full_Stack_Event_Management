import React , {useState , useContext} from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

const authContext = React.createContext()



const AuthContextProvider = ({children}) => {

    const 
  
    const [userMail , setUserMail] = useState(localStorage.getItem("userMail") || null);

    if (userMail){

    }


    const signup = async ({signupCredentials})=>{

    }
    
  return (
    <authContext.Provider>
        {children}
    </authContext.Provider>
  )
}

export default AuthContext
