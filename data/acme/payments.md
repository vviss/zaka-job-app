# Payments Overview

The payments stack has two parts. The current system is the Unified Billing service, which handles all live invoicing and metering. It replaced an older component during the current fiscal year.

The older component, the LegacyBilling service, is deprecated. It still runs in read only mode for historical invoice lookups, but no new traffic is routed to it and it is scheduled for shutdown once the migration completes. Teams should not build anything new against LegacyBilling.

For questions about who maintains a given service, see the services directory document, which lists current ownership for every service in the payments area.
