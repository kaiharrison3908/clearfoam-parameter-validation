// compute explicit time derivative
volScalarField ddtE_field = fvc::ddt(E);

// create a dimensionless switch field (1 if E is decreasing, else 0)
volScalarField switchField
(
    IOobject
    (
        "switchField",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    mesh,
    dimensionedScalar("zero", dimless, 0.0) // initialize to 0
);

scalar t = runTime.value();

// fill cell by cell
forAll(ddtE_field, cellI)
{
    // if (ddtE_field[cellI] < -1.0e-6 && t>5000) // if E is decreasing
    switchField[cellI] = 1.0; // dimensionless
}

volScalarField A_dimless_ = max(A / tau, SMALL);
volScalarField hill_ = eta1*pow(A, n) / (pow(tau, n) + pow(A, n));

volScalarField decayCoeff = eta1 * hill_;
volScalarField growthCoeff = mu * C / (k_1 + C);

fvScalarMatrix MEqn
(
    fvm::ddt(M)
    - fvm::laplacian(d2, M, "laplacian(d2,M)")
    ==
    (
        
        fvm::Sp(mu*C/(k_1+C), M)
        - fvm::Sp(k_4, M)
        - fvm::Sp(hill_, M)
        + fvm::Sp(eta2*N/(k5+M), M)
        - fvm::Sp(delta_death*max(scalar(0), (E_crit - E)/E_crit) * switchField, M) 
    )
);

solve(MEqn);

ddtM = gMax(mag(fvc::ddt(M)())())/(gMax(M)+SMALL); // clip growth rate 
