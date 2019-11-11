# astrokat
General observational tools for astronomy observations with the MeerKAT telescope

Specifying terminology and functionality that is incorporated into the observation framework in
relation to observational requirements.

Most requirements and implementations are derived from usage cases provided by MeerKAT staff
scientists.

Use documentation can be found on the [wiki pages](https://github.com/ska-sa/astrokat/wiki)

## Installation instruction
`pip install argcomplete`


## Autocomplete script input arguments
Helper script input arguments follow a very verbose naming convention.
To enable auto-complete of the long python input arguments
eval "$(register-python-argcomplete astrokat-catalogue2observation.py)"

This will enable completion in Bash.  To try it out, do:
`astrokat-catalogue2observation.py <TAB><TAB>`
This should display all you argument options

