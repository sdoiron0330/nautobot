import { Button, FormControl, FormLabel, Input, Link, Box } from "@nautobot/nautobot-ui"
import axios from "axios"

import { useGetSessionQuery } from "@utils/apiSlice";
import { useNavigate } from "react-router-dom";

axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default function Login() {
  const { refetch: refetchSession } = useGetSessionQuery();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post(
      '/api/users/tokens/authenticate/', {
        username: e.target.username.value,
        password: e.target.password.value,
      })
      .then(() => {
        refetchSession().then(() => {navigate("/")});

      })
      .catch(err => alert(err.detail))
  }

  
  return (
      <Box boxShadow='base' p='6' rounded='md' bg='white'>
        <form method="POST" onSubmit={handleSubmit}>
              <FormControl>
                <FormLabel>Username</FormLabel>
                <Input isRequired={true} name="username"></Input>
              </FormControl>
              <FormControl>
                <FormLabel>Password</FormLabel>
                <Input isRequired={true} name="password" type="password"></Input>
              </FormControl>
              <Button type="submit">Log In</Button>
        </form>
      </Box>
  )
}

// { isSuccess && sessionInfo.backends.length > 0 ?
//   sessionInfo.backends.map((backend, idx) => { return (<Link key={idx} href={backend}>Login with {backend}</Link>) })
// : <></> }