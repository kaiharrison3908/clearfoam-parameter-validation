

if (adjustTimeStep)
{

    scalar dtForM = dtManagerM.computeTimestep();
    scalar dtForC = dtManagerC.computeTimestep();
    scalar dtForA = dtManagerA.computeTimestep();
    scalar dtForN = dtManagerN.computeTimestep();


    runTime.setDeltaT
    (
	min
	(
	    min(dtForN, min(dtForA, min(dtForM, dtForC))),
	    min(1.2*runTime.deltaTValue(),maxDeltaT)
	)
    );
      
    Info << "deltaT = " <<  runTime.deltaTValue() << endl;
}

// ************************************************************************* //
