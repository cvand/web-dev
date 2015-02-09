$(function() {
	var $posts_wrapper = $("#posts-wrapper"), 
	$posts_list = $("#posts-list"), 
	baseHeight = 0, $el;

	$posts_wrapper.height($posts_wrapper.height());
	baseHeight = $posts_wrapper.height() - $posts_list.height();

	$("#posts-list").delegate("a.delete-action", "click", function() {
		_link = $(this).attr("href");
		loadPosts(_link);
		return false;
	});

	function loadPosts(href) {
		$posts_wrapper.find("#posts-list").fadeOut(200, function() {
			$posts_list.hide().load( href + " #posts-list", function() {
				$posts_list.fadeIn(200, function() {
					$posts_wrapper.animate({
						height : baseHeight + $posts_list.height() + "px"
					});
				});
			});
		});

	}

});
