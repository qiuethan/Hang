/*
Author: Ethan Qiu
Filename: Navbar.js
Last Modified: June 7, 2023
Description: Display Navigation Bar
*/

//From https://mui.com/material-ui/react-drawer/
import React, { useState, useEffect } from 'react';
import {useNavigate} from 'react-router-dom';
import { useSelector } from 'react-redux';

import { styled, useTheme } from "@mui/material/styles";
import MuiDrawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import EventIcon from '@mui/icons-material/Event';
import CloseIcon from "@mui/icons-material/Close";
import ChatIcon from '@mui/icons-material/Chat';
import PeopleIcon from '@mui/icons-material/People';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import CreateIcon from '@mui/icons-material/Create';

import logo from '../../images/logo.svg';

//Configure Opened Navbar Width
const drawerWidth = 240;

//Configure Navbar Open Style
const openedMixin = (theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen
  }),
  overflowX: "hidden"
});

//Configure Navbar Closed Style
const closedMixin = (theme) => ({
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen
  }),
  overflowX: "hidden",
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up("sm")]: {
    width: `calc(${theme.spacing(8)} + 1px)`
  }
});

//Configure Drawer Toolbar Icon
const DrawerHeader = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar
}));

//Configure Drawer Functionality
const Drawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "open"
})(({ theme, open }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: "nowrap",
  boxSizing: "border-box",
  ...(open && {
    ...openedMixin(theme),
    "& .MuiDrawer-paper": openedMixin(theme)
  }),
  ...(!open && {
    ...closedMixin(theme),
    "& .MuiDrawer-paper": closedMixin(theme)
  })
}));

//Get and return window dimensions
const getWindowDimensions = () => {
  const { innerWidth: width, innerHeight: height } = window;
  return{
    width,
    height
  };
}

//Apply window dimensions + window resize
const useWindowDimensions = () => {
  //Define windowDimension state variable
  const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

  //On render
  useEffect(() => {
    const handleResize = () => {
      setWindowDimensions(getWindowDimensions());
    }
    //If resized
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowDimensions
}

//Navbar component
const Navbar = ({ setCurrentPage }) => {

    //Define user state variable
    const [user, setUser] = useState(JSON.parse(localStorage.getItem('profile')));

    //Define navigation variable
    const history = useNavigate();

    //On render
    useEffect(() => {
      setUser(JSON.parse(localStorage.getItem('profile')));
    }, [useSelector((state) => state)])

    //Get window dimensions
    const {height, width} = useWindowDimensions();

    //When home clicked
    const home = () => {
        history("/");
        setCurrentPage("home");
    }

    //When chat clicked
    const chat = () => {
        history("/chat");
        setCurrentPage("chat");
    }

    //When hang clicked
    const hang = () => {
        history("/hang");
        setCurrentPage("hang");
    }

    //When create clicked
    const create = () => {
        history("/hang/create");
        setCurrentPage("create");
    }

    //When friends clicked
    const friends = () => {
        history("/friends");
        setCurrentPage("friends");
    }

    //When profile clicked
    const profile = () => {
        history("/profile");
        setCurrentPage("profile");
    }

    //Apply theme
    const theme = useTheme();
    const [open, setOpen] = React.useState(false);

    //When drawer toolbox clicked
    const handleDrawer = () => {
        if (open) {
        handleDrawerClose();
        } else {
        handleDrawerOpen();
        }
    };

    //Open drawer
    const handleDrawerOpen = () => {
        setOpen(true);
    };

    //Close drawer
    const handleDrawerClose = () => {
        setOpen(false);
    };

    //Render components
    return(
      <Drawer variant="permanent" open={open} sx={{height : '100%'}}>
        <DrawerHeader>
          <IconButton onClick={handleDrawer}>
            {open ? <CloseIcon /> : <MenuIcon />}
          </IconButton>
        </DrawerHeader>
        <List sx={{height : '100%'}}>
          <ListItem key={"logo"} disablePadding sx={{display: "block"}}>
            <ListItemButton
              sx={{
                minHeight: 48,
                justifyContent: open ? "initial" : "center",
                px: 2.5
              }}
              onClick={home}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 3 : "auto",
                  justifyContent: "center"
                }}
              >
                <img src={logo} style={{height: "24px", width: "24px"}}/>
              </ListItemIcon>
              <ListItemText primary={"Home"} sx={{ opacity: open ? 1 : 0}}/>
            </ListItemButton>
          </ListItem>
            {user !== null &&
                <ListItem key={"hangs"} disablePadding sx={{display: "block"}}>
                    <ListItemButton
                        sx={{
                            minHeight: 48,
                            justifyContent: open ? "initial" : "center",
                            px: 2.5
                        }}
                        onClick={hang}
                    >
                        <ListItemIcon
                            sx={{
                                minWidth: 0,
                                mr: open ? 3 : "auto",
                                justifyContent: "center"
                            }}
                        >
                            <EventIcon/>
                        </ListItemIcon>
                        <ListItemText primary={"View Hang Events"} sx={{ opacity: open ? 1 : 0}}/>
                    </ListItemButton>
                </ListItem>
            }
            {user !== null &&
                <ListItem key={"create"} disablePadding sx={{display: "block"}}>
                    <ListItemButton
                        sx={{
                            minHeight: 48,
                            justifyContent: open ? "initial" : "center",
                            px: 2.5
                        }}
                        onClick={create}
                    >
                        <ListItemIcon
                            sx={{
                                minWidth: 0,
                                mr: open ? 3 : "auto",
                                justifyContent: "center"
                            }}
                        >
                            <CreateIcon/>
                        </ListItemIcon>
                        <ListItemText primary={"Create Hang"} sx={{ opacity: open ? 1 : 0}}/>
                    </ListItemButton>
                </ListItem>
            }
          {user !== null &&
            (
              <ListItem key={"chat"} disablePadding sx={{display: "block"}}>
                <ListItemButton
                  sx={{
                    minHeight: 48,
                    justifyContent: open ? "initial" : "center",
                    px: 2.5
                  }}
                  onClick={chat}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: open ? 3 : "auto",
                      justifyContent: "center"
                    }}
                  >
                    <ChatIcon/>
                  </ListItemIcon>
                  <ListItemText primary={"Chat"} sx={{ opacity: open ? 1 : 0}}/>
                </ListItemButton>
              </ListItem>
            )
          }
          {user !== null &&
            <ListItem key={"friends"} disablePadding sx={{display: "block"}}>
              <ListItemButton
                sx={{
                  minHeight: 48,
                  justifyContent: open ? "initial" : "center",
                  px: 2.5
                }}
                onClick={friends}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : "auto",
                    justifyContent: "center"
                  }}
                >
                  <PeopleIcon/>
                </ListItemIcon>
                <ListItemText primary={"Friends"} sx={{ opacity: open ? 1 : 0}}/>
              </ListItemButton>
            </ListItem>
          }

          {user !== null &&
            <ListItem key={"account"} disablePadding sx={{display: "block", position: height >= 264 ? "absolute" : "relative", bottom: 0}}>
              <ListItemButton
                sx={{
                  minHeight: 48,
                  justifyContent: open ? "initial" : "center",
                  px: 2.5
                }}
                onClick={profile}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : "auto",
                    justifyContent: "center"
                  }}
                >
                  <AccountCircleIcon/>
                </ListItemIcon>
                <ListItemText primary={"Account"} sx={{ opacity: open ? 1 : 0}}/>
              </ListItemButton>
            </ListItem>
          }
        </List>
        
      </Drawer>
    );
};

export default Navbar;