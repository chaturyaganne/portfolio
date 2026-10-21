/* Pure pricing and eligibility rules. Currency is held in integer cents. */
(() => {
 'use strict';
 const priceFor=(seat,quantity)=>({each:seat.base+seat.fee,base:seat.base*quantity,fees:seat.fee*quantity,total:(seat.base+seat.fee)*quantity});
 const fits=(seat,needs)=>seat.available>=needs.quantity&&(seat.base+seat.fee)<=needs.budget*100&&(!needs.stepFree||seat.stepFree)&&(!needs.clearView||seat.clearView);
 window.EncoreDomain=Object.freeze({priceFor,fits});
})();
