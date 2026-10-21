/* Fictional sample content, shared by the prototype and tests. */
(() => {
'use strict';
 const events=[
  {id:'midnight',name:'Midnight Echo',category:'Music',date:'MAY 14, 2027',venue:'Harbor Hall',place:'New York, NY',art:'moss',tag:'An evening worth staying out for',offset:0},
  {id:'city',name:'City Lights FC',category:'Sports',date:'MAY 16, 2027',venue:'Riverside Field',place:'Brooklyn, NY',art:'red',tag:'For the love of the game',offset:600},
  {id:'laugh',name:'The Late Laugh',category:'Comedy',date:'MAY 21, 2027',venue:'The Little Room',place:'New York, NY',art:'violet',tag:'A very good reason to go out',offset:-800},
  {id:'blue',name:'Blue Hour Sessions',category:'Music',date:'MAY 23, 2027',venue:'Hudson Studio',place:'New York, NY',art:'blue',tag:'Small room. Big sound.',offset:-400},
  {id:'summer',name:'Summer at the Pier',category:'Music',date:'JUN 04, 2027',venue:'Sunset Pavilion',place:'Brooklyn, NY',art:'ochre',tag:'Your first summer memory',offset:1200},
  {id:'courtside',name:'Courtside Sundays',category:'Sports',date:'JUN 06, 2027',venue:'Eastside Arena',place:'Queens, NY',art:'rust',tag:'Bring your people',offset:400}
 ];
 const inventory=[
  {id:'a',section:'102',row:'B',base:6400,fee:1600,available:6,stepFree:true,clearView:true,view:'Clear view',route:'Step-free route',seatType:'Standard seats; wheelchair space not confirmed'},
  {id:'b',section:'104',row:'D',base:7800,fee:1800,available:4,stepFree:true,clearView:true,view:'Clear view',route:'Step-free route',seatType:'Standard seats; wheelchair space not confirmed'},
  {id:'c',section:'203',row:'A',base:4900,fee:1300,available:5,stepFree:false,clearView:false,view:'Partial view',route:'Stairs on route',seatType:'Standard seats'},
  {id:'d',section:'105',row:'F',base:7400,fee:1800,available:6,stepFree:false,clearView:true,view:'Clear view',route:'Stairs on route',seatType:'Standard seats'},
  {id:'e',section:'101',row:'C',base:9600,fee:2200,available:2,stepFree:true,clearView:true,view:'Clear view',route:'Step-free route',seatType:'Standard seats; wheelchair space not confirmed'},
  {id:'f',section:'205',row:'G',base:6100,fee:1500,available:4,stepFree:true,clearView:false,view:'Partial view',route:'Step-free route',seatType:'Standard seats; wheelchair space not confirmed'}
 ];

 window.EncoreCatalog=Object.freeze({events,inventory});
})();
