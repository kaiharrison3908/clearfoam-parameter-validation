dimensionedScalar D_bulk (
    "D_bulk",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    0.0001 / 86400     
);
dimensionedScalar D_biofilm (
    "D_biofilm",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    0.00008 / 86400   
);

volScalarField Mtot = min(E, scalar(1.0));       // non dimensional

// Build a tmp<volScalarField> for the spatial D field 
tmp<volScalarField> Dtmp = D_bulk*(1.0 - Mtot) + D_biofilm*Mtot;

// Construct the actual volScalarField from that tmp 
volScalarField D
(
    IOobject
    (
        "D",                    // field name
        runTime.timeName(),     
        mesh,                   
        IOobject::NO_READ,      
        IOobject::AUTO_WRITE
    ),
    Dtmp                        
);

// Build the consumption rate parameter Rmax
dimensionedScalar Rmax_m = mu*M_inf/Y;  
dimensionedScalar Rmax_e = mu_e*E_inf/Y_e;  

fvScalarMatrix CEqn
(
    fvm::ddt(C)
  - fvm::laplacian(D, C)
  ==
    - fvm::Sp( Rmax_m * Mtot/(k_1 + C)+Rmax_e * E/(k_1 + C), C )
);

solve(CEqn);
