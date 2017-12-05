<?php
	$query=mysql_query("SELECT * from TABLE_NAME WHERE itemName LIKE '%$itemName%' AND price<='$maxPrice'order by price asc");

?>