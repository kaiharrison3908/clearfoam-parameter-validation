dimensionedScalar Die_bulk (
    "Die_bulk",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    0.0000078 / 86400 
); // slower than autoinducer

dimensionedScalar Die_biofilm (
    "Die_biofilm",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    0.0000000039 / 86400 
); // much slower than bulk

tmp<volScalarField> Dietmp = Die_bulk*(1.0 - min(E, scalar(1.0))) + Die_biofilm*(min(E, scalar(1.0)));

volScalarField Die
(
    IOobject
    (
        "Die",                    
        runTime.timeName(),     
        mesh,                  
        IOobject::NO_READ,      
        IOobject::AUTO_WRITE
    ),
    Dietmp                        
);

// equation implementation
fvScalarMatrix IeEqn
(
    fvm::ddt(Ie)
  - fvm::laplacian(Die, Ie)
  ==
    M_b * K_I * I
    - fvm::Sp( gamma_Ie, Ie)
);

solve(IeEqn);
