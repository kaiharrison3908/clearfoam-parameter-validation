// Main run loop that computes derivatives and updates fields

#include <iostream>
#include <fstream>
#include "fvCFD.H"
#include "timestepManager.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //


int main(int argc, char *argv[])
{

    argList::addOption("zmax", "zmax");
    
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "readTimeControls.H"
    
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info << "\nStarting time loop\n" << endl;

    #include "initOptionZ.H"
    
    while (runTime.run())
    {

	#include "setDeltaT.H"
	
	runTime++;
      
	Info << "Time = " << runTime.timeName() << endl;
		
	#include "CEqn.H"
	#include "updateDiffusion.H"
	#include "MEqn.H"
    #include "AEqn.H"
    #include "NEqn.H"
    #include "EEqn.H"
    #include "IEqn.H"
    #include "IeEqn.H"
	#include "updateBiofilmPhase.H"

	dtManagerC.updateDerivatives();
    Info << "C in [" << gMin(C) << ";" << gMax(C) << "]" << endl;

	dtManagerM.updateDerivatives();
	
	Info << "M in [" << gMin(M) << ";" << gMax(M) << "]" << endl;

    dtManagerA.updateDerivatives();
	
	Info << "A in [" << gMin(A)*1e09 << ";" << gMax(A)*1e09 << "]" << endl;

    dtManagerN.updateDerivatives();
	
	Info << "N in [" << gMin(N) << ";" << gMax(N) << "]" << endl;
	
    dtManagerE.updateDerivatives();
	
	Info << "E in [" << gMin(E) << ";" << gMax(E) << "]" << endl;

    dtManagerI.updateDerivatives();
	
	Info << "I in [" << gMin(I) << ";" << gMax(I) << "]" << endl;

    dtManagerIe.updateDerivatives();

    Info << "Ie in [" << gMin(Ie) << ";" << gMax(Ie) << "]" << endl;


	runTime.write();

	runTime.printExecutionTime(Info);

	#include "checkOptionZ.H"
      
    }

    Info << "End\n" << endl;

    return 0;
    
}


// ************************************************************************* //
