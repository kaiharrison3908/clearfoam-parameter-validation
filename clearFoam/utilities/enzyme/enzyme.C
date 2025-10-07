#include "fvCFD.H"
#include <iostream>
#include <fstream>

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Post-processing utility to extract enzyme concentration data for dispersal analysis
int main(int argc, char *argv[])
{

    std::ofstream bfile;
    bfile.open ("enzyme.dat");
    
    Foam::timeSelector::addOptions();  
    Foam::argList args(argc,argv); 

    #include "createTime.H"
    Foam::instantList timeDirs = Foam::timeSelector::select0(runTime, args);

    forAll(timeDirs, timei)
    {
        runTime.setTime(timeDirs[timei], timei);
    
        #include "createMesh.H"

        Info << "Reading Ie" << endl;
        volScalarField Ie
        (
            IOobject
            (
                "Ie",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );

        scalar tau = 1;

        volScalarField Ie_dimless
        (
            IOobject
            (
                "Ie_dimless",
                runTime.timeName(),
                mesh,
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            Ie / tau
        );

        // Cell volumes
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

        // Compute volume-weighted average of Ie/τ
        dimensionedScalar Ieavg_dimless =
            dimensionedScalar("Ieavg_dimless", Ie.dimensions() / dimTime, gSum(Ie_dimless.primitiveField() * mesh.V()) / domainVolume.value());

        Info << "Ieavg_dimless = " << Ieavg_dimless.value() << endl;
        bfile << runTime.timeName() << " " << Ieavg_dimless.value() << "\n";

        Info << endl;
    }
	
    Info << nl << "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
         << "  ClockTime = " << runTime.elapsedClockTime() << " s"
         << nl << endl;

    Info << "End\n" << endl;

    return 0;
}

// ************************************************************************* //
