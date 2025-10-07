#include "fvCFD.H"
#include <iostream>
#include <fstream>

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Post-processing utility to calculate total biomass volume over time
int main(int argc, char *argv[])
{

    std::ofstream bfile;
    bfile.open ("biomass.dat");
    
    Foam::timeSelector::addOptions();  
    Foam::argList args(argc,argv); 

    #include "createTime.H"
    Foam::instantList timeDirs = Foam::timeSelector::select0(runTime, args);

    // int last = timeDirs.size()-1;
    // runTime.setTime(timeDirs[last], last);
    
    forAll(timeDirs, timei)
    {
	
	runTime.setTime(timeDirs[timei], timei);
    
	#include "createMesh.H"

	Info << "Reading M" << endl;
	volScalarField M
	(
	    IOobject
	    (
		"M",
		runTime.timeName(),
		mesh,
		IOobject::MUST_READ,
		IOobject::AUTO_WRITE
	    ),
	    mesh
	);

	// volume

	volScalarField cellVolume
	(
	    IOobject
	    (
		"cellVolume",
		runTime.timeName(),
		mesh,
		IOobject::NO_READ,
		IOobject::AUTO_WRITE
	    ),
	    mesh,
	    dimensionedScalar("zero",dimVolume,0.0)
	);

	cellVolume.ref() = mesh.V();

	dimensionedScalar domainVolume = gSum(cellVolume);

	// biomass

	dimensionedScalar biomassVolume = 0.*domainVolume;

	forAll(M, celli) {
	    if(M[celli] > SMALL) {
		biomassVolume += cellVolume.ref()[celli];
	    }
	}

	reduce(biomassVolume, sumOp<dimensionedScalar>());
	
	biomassVolume = biomassVolume/domainVolume;
	Info << "biomass = " << biomassVolume.value() << endl;
	
	// write

	bfile << runTime.timeName() << " " << biomassVolume.value() << "\n";

	Info << endl;
	
    }
	
    Info << nl << "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
	<< "  ClockTime = " << runTime.elapsedClockTime() << " s"
	<< nl << endl;

    Info << "End\n" << endl;

    return 0;
    
}


// ************************************************************************* //
