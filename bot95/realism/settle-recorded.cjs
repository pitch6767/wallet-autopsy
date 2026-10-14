function settleRecorded(snapshot,{winner,closed,resolved,evidence,at}){
  if(!closed||!resolved||!['Up','Down'].includes(winner)||!evidence||
    !Number.isFinite(at)||!Number.isFinite(snapshot.expiredAt)||at<snapshot.expiredAt||
    ![snapshot.quantities?.Up,snapshot.quantities?.Down,snapshot.cost,snapshot.fees].every(Number.isFinite)||
    snapshot.error||snapshot.issues?.length)throw Error('Confirmed valid settlement required');
  if(snapshot.settlementPnl!==null){
    if(snapshot.winner!==winner)throw Error('Conflicting settlement');
    return snapshot;
  }
  return {...snapshot,winner,settlementAt:at,settlementEvidence:evidence,
    exposureMs:snapshot.exposureMs+(snapshot.unmatched>1e-8?at-snapshot.expiredAt:0),
    settlementPnl:snapshot.quantities[winner]-snapshot.cost-snapshot.fees};
}
module.exports={settleRecorded};
